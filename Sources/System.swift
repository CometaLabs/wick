import Foundation
import IOKit.pwr_mgt
import IOKit.ps

// MARK: - Hooks de Claude Code en ~/.claude/settings.json

enum HookInstaller {
    static let events = ["SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse",
                         "Notification", "Stop", "SubagentStop", "PreCompact", "SessionEnd"]
    private static let toolEvents: Set<String> = ["PreToolUse", "PostToolUse"]
    private static let marker = "/.wick/hook"

    enum Failure: Error { case unreadableSettings }

    /// El script del hook apunta al binario actual de la app; se reescribe en cada arranque.
    static func writeHookScript() {
        WickPaths.ensure()
        let exe = Bundle.main.executablePath ?? "/Applications/Wick.app/Contents/MacOS/Wick"
        let script = """
        #!/bin/sh
        # Wick: le cuenta a la app qué hace Claude Code. Nunca bloquea ni cambia nada.
        APP='\(exe.replacingOccurrences(of: "'", with: "'\\''"))'
        [ -x "$APP" ] && exec "$APP" --hook
        cat >/dev/null
        exit 0

        """
        let url = WickPaths.hookScript
        try? script.write(to: url, atomically: true, encoding: .utf8)
        chmod(url.path, 0o755)
    }

    private static func readSettings() throws -> [String: Any] {
        let url = WickPaths.claudeSettings
        guard FileManager.default.fileExists(atPath: url.path) else { return [:] }
        let data = try Data(contentsOf: url)
        if data.isEmpty { return [:] }
        guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw Failure.unreadableSettings
        }
        return obj
    }

    private static func writeSettings(_ settings: [String: Any]) throws {
        // Si settings.json es un enlace (dotfiles), se escribe en el archivo real.
        let url = WickPaths.claudeSettings.resolvingSymlinksInPath()
        try FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        let backup = url.appendingPathExtension("wick-backup")
        if FileManager.default.fileExists(atPath: url.path) && !FileManager.default.fileExists(atPath: backup.path) {
            try? FileManager.default.copyItem(at: url, to: backup)
        }
        let data = try JSONSerialization.data(withJSONObject: settings,
                                              options: [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes])
        try data.write(to: url, options: .atomic)
    }

    private static func isOurs(_ group: Any) -> Bool {
        guard let g = group as? [String: Any], let hooks = g["hooks"] as? [[String: Any]] else { return false }
        return hooks.contains { ($0["command"] as? String)?.contains(marker) == true }
    }

    static func isInstalled() -> Bool {
        guard let settings = try? readSettings(), let hooks = settings["hooks"] as? [String: Any] else { return false }
        return events.allSatisfy { event in (hooks[event] as? [Any])?.contains(where: isOurs) == true }
    }

    static func install() throws {
        writeHookScript()
        var settings = try readSettings()
        var hooks = settings["hooks"] as? [String: Any] ?? [:]
        let command = "\"\(WickPaths.hookScript.path)\""
        for event in events {
            var groups = (hooks[event] as? [Any] ?? []).filter { !isOurs($0) }
            var group: [String: Any] = ["hooks": [["type": "command", "command": command, "timeout": 5]]]
            if toolEvents.contains(event) { group["matcher"] = "*" }
            groups.append(group)
            hooks[event] = groups
        }
        settings["hooks"] = hooks
        try writeSettings(settings)
    }

    static func uninstall() throws {
        var settings = try readSettings()
        guard var hooks = settings["hooks"] as? [String: Any] else { return }
        for (event, value) in hooks {
            guard let groups = value as? [Any] else { continue }
            let kept = groups.filter { !isOurs($0) }
            if kept.isEmpty { hooks.removeValue(forKey: event) } else { hooks[event] = kept }
        }
        if hooks.isEmpty { settings.removeValue(forKey: "hooks") } else { settings["hooks"] = hooks }
        try writeSettings(settings)
    }
}

// MARK: - Mantener el Mac despierto (aserciones de IOKit, sin procesos externos)

final class AwakeHold {
    private let type: String
    private var id: IOPMAssertionID = 0
    private(set) var held = false

    init(displayToo: Bool) {
        type = displayToo ? kIOPMAssertPreventUserIdleDisplaySleep : kIOPMAssertPreventUserIdleSystemSleep
    }

    func set(_ on: Bool, reason: String) {
        if on && !held {
            held = IOPMAssertionCreateWithName(type as CFString, IOPMAssertionLevel(kIOPMAssertionLevelOn),
                                               reason as CFString, &id) == kIOReturnSuccess
        } else if !on && held {
            IOPMAssertionRelease(id)
            held = false
        }
    }
}

enum Power {
    /// (en batería, porcentaje)
    static func battery() -> (onBattery: Bool, percent: Int?) {
        guard let info = IOPSCopyPowerSourcesInfo()?.takeRetainedValue() else { return (false, nil) }
        let providing = IOPSGetProvidingPowerSourceType(info)?.takeUnretainedValue() as String?
        let onBattery = providing == kIOPMBatteryPowerKey
        guard let list = IOPSCopyPowerSourcesList(info)?.takeRetainedValue() as? [CFTypeRef] else {
            return (onBattery, nil)
        }
        for source in list {
            guard let desc = IOPSGetPowerSourceDescription(info, source)?.takeUnretainedValue() as? [String: Any],
                  let current = desc[kIOPSCurrentCapacityKey] as? Int,
                  let max = desc[kIOPSMaxCapacityKey] as? Int, max > 0 else { continue }
            return (onBattery, current * 100 / max)
        }
        return (onBattery, nil)
    }

    static var lowBattery: Bool {
        let b = battery()
        return b.onBattery && (b.percent ?? 100) <= 15
    }

    /// `pmset -a disablesleep 1` sobrevive a reinicios: hay que poder detectarlo.
    static func sleepDisabled() -> Bool {
        guard let out = run("/usr/bin/pmset", ["-g"]) else { return false }
        for line in out.split(separator: "\n") where line.contains("SleepDisabled") {
            return line.split(whereSeparator: { $0 == " " || $0 == "\t" }).last == "1"
        }
        return false
    }

    static func run(_ path: String, _ args: [String]) -> String? {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: path)
        p.arguments = args
        let pipe = Pipe()
        p.standardOutput = pipe
        p.standardError = FileHandle.nullDevice
        do { try p.run() } catch { return nil }
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        p.waitUntilExit()
        return String(data: data, encoding: .utf8)
    }

    /// Ejecuta como administrador (macOS pide la contraseña). Devuelve la salida, o nil si se canceló o falló.
    @discardableResult
    static func runAsAdmin(_ command: String) -> String? {
        let escaped = command.replacingOccurrences(of: "\\", with: "\\\\").replacingOccurrences(of: "\"", with: "\\\"")
        var error: NSDictionary?
        let result = NSAppleScript(source: "do shell script \"\(escaped)\" with administrator privileges")?
            .executeAndReturnError(&error)
        return error == nil ? (result?.stringValue ?? "") : nil
    }

    static func shellQuote(_ s: String) -> String {
        "'" + s.replacingOccurrences(of: "'", with: "'\\''") + "'"
    }
}

// MARK: - Tapa cerrada: un vigilante con permisos de administrador que obedece a un fichero

final class LidController {
    private(set) var running = false
    private var lastWant: Bool?
    private var lastCheck = Date.distantPast

    private var pid: Int32 {
        get { Int32(UserDefaults.standard.integer(forKey: "lidWatcherPID")) }
        set { UserDefaults.standard.set(Int(newValue), forKey: "lidWatcherPID") }
    }

    /// El script viaja dentro de la llamada (`sh -c`), no como fichero: así nadie puede
    /// cambiarlo en el paquete de la app antes de que se ejecute como root.
    /// Solo desactiva el reposo al cerrar la tapa mientras WANT empieza por «1».
    /// Al salir (app cerrada o colgada, STOP, señal o batería ≤ 15 %) deja `disablesleep 0`.
    static let script = #"""
    APP_PID="$1"; WANT="$2"; STOP="$3"; current=""
    apply() { [ "$1" = "$current" ] && return; /usr/bin/pmset -a disablesleep "$1"; current="$1"; }
    restore() { /usr/bin/pmset -a disablesleep 0; exit 0; }
    trap restore HUP INT TERM
    apply 0; n=0; low=0
    while /bin/kill -0 "$APP_PID" 2>/dev/null && [ ! -e "$STOP" ]; do
      if [ $((n % 30)) -eq 0 ]; then
        low=0
        b=$(/usr/bin/pmset -g batt)
        case "$b" in *"Battery Power"*)
          p=$(printf '%s\n' "$b" | /usr/bin/sed -n 's/^.*[^0-9]\([0-9][0-9]*\)%;.*$/\1/p' | /usr/bin/head -n 1)
          [ -n "$p" ] && [ "$p" -le 15 ] && low=1 ;;
        esac
      fi
      n=$((n + 1)); want=0
      if [ "$low" -eq 0 ] && [ -f "$WANT" ] && [ "$(/usr/bin/head -c 1 "$WANT")" = "1" ]; then want=1; fi
      apply "$want"
      /bin/sleep 1
    done
    restore
    """#

    /// Pide la contraseña una vez y deja el vigilante corriendo mientras la app siga abierta.
    func start() -> Bool {
        if isRunning() { running = true; return true }
        WickPaths.ensure()
        try? FileManager.default.removeItem(at: WickPaths.lidStop)
        write(false)
        let app = ProcessInfo.processInfo.processIdentifier
        let cmd = "nohup /bin/sh -c \(Power.shellQuote(Self.script)) wick-lid \(app) "
            + "\(Power.shellQuote(WickPaths.lidWant.path)) \(Power.shellQuote(WickPaths.lidStop.path)) "
            + ">/dev/null 2>&1 & echo $!"
        guard let out = Power.runAsAdmin(cmd), let watcher = Int32(out.trimmingCharacters(in: .whitespacesAndNewlines)) else {
            running = false
            return false
        }
        pid = watcher
        running = true
        return true
    }

    func stop() {
        guard running else { return }
        FileManager.default.createFile(atPath: WickPaths.lidStop.path, contents: Data())
        write(false)
        running = false
    }

    func want(_ on: Bool) {
        guard running, lastWant != on else { return }
        write(on)
    }

    private func write(_ on: Bool) {
        lastWant = on
        try? (on ? "1" : "0").write(to: WickPaths.lidWant, atomically: true, encoding: .utf8)
    }

    /// Cada pocos segundos: ¿sigue vivo el vigilante?
    func refresh() {
        guard Date().timeIntervalSince(lastCheck) > 5 else { return }
        lastCheck = Date()
        running = isRunning()
    }

    /// Es nuestro si el PID existe (aunque sea de root) y su línea de órdenes es la del vigilante.
    func isRunning() -> Bool {
        let watcher = pid
        guard watcher > 1, kill(watcher, 0) == 0 || errno == EPERM else { return false }
        return Power.run("/bin/ps", ["-p", String(watcher), "-o", "args="])?.contains("wick-lid") == true
    }
}
