import Foundation
import Darwin

// MARK: - Rutas compartidas entre la app y el hook

enum WickPaths {
    static let home = FileManager.default.homeDirectoryForCurrentUser
    static let root = home.appendingPathComponent(".wick", isDirectory: true)
    static let sessions = root.appendingPathComponent("sessions", isDirectory: true)
    static let hookScript = root.appendingPathComponent("hook")
    static let lidWant = root.appendingPathComponent("lid-want")
    static let lidStop = root.appendingPathComponent("lid-stop")
    /// WICK_CLAUDE_SETTINGS permite probar el instalador contra otro archivo.
    static let claudeSettings = ProcessInfo.processInfo.environment["WICK_CLAUDE_SETTINGS"]
        .map { URL(fileURLWithPath: $0) } ?? home.appendingPathComponent(".claude/settings.json")

    static func ensure() {
        try? FileManager.default.createDirectory(at: sessions, withIntermediateDirectories: true)
    }
}

enum AgentState: String, Codable {
    case working, waiting, idle
}

struct SessionRecord: Codable {
    var id: String
    var state: AgentState
    var cwd: String?
    var pid: Int32?
    var since: Date
    var updated: Date
    var event: String
    /// nil = Claude Code por hooks; si no, el agente detectado por proceso.
    var agent: String? = nil

    var agentName: String { agent ?? "Claude Code" }

    var project: String {
        guard let cwd = cwd, !cwd.isEmpty, cwd != "/" else { return agentName }
        return URL(fileURLWithPath: cwd).lastPathComponent
    }
}

private let encoder: JSONEncoder = {
    let e = JSONEncoder()
    e.dateEncodingStrategy = .secondsSince1970
    return e
}()

private let decoder: JSONDecoder = {
    let d = JSONDecoder()
    d.dateDecodingStrategy = .secondsSince1970
    return d
}()

// MARK: - Modo hook: Claude Code llama a `Wick --hook` con un JSON por stdin

enum HookCLI {
    /// Nunca escribe en stdout ni sale con error: Claude Code no debe notar nada.
    static func run() -> Never {
        let data = FileHandle.standardInput.readDataToEndOfFile()
        guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let rawID = obj["session_id"] as? String else { exit(0) }
        let id = String(rawID.filter { $0.isLetter || $0.isNumber || $0 == "-" || $0 == "_" }.prefix(80))
        guard !id.isEmpty else { exit(0) }

        WickPaths.ensure()
        let file = WickPaths.sessions.appendingPathComponent(id + ".json")
        let event = obj["hook_event_name"] as? String ?? ""

        if event == "SessionEnd" {
            try? FileManager.default.removeItem(at: file)
            exit(0)
        }

        let state: AgentState
        switch event {
        case "UserPromptSubmit", "PreToolUse", "PostToolUse", "SubagentStop", "PreCompact":
            state = .working
        case "Notification":
            // permission_prompt / elicitation: te necesita. idle_prompt: ya había terminado.
            let kind = obj["notification_type"] as? String ?? ""
            let message = (obj["message"] as? String ?? "").lowercased()
            state = (kind == "idle_prompt" || message.contains("waiting for your input")) ? .idle : .waiting
        case "Stop", "SessionStart":
            state = .idle
        default:
            exit(0)
        }

        let now = Date()
        var record = (try? Data(contentsOf: file)).flatMap { try? decoder.decode(SessionRecord.self, from: $0) }
            ?? SessionRecord(id: id, state: state, cwd: nil, pid: nil, since: now, updated: now, event: event)
        if record.state != state {
            record.state = state
            record.since = now
        }
        record.updated = now
        record.event = event
        if let cwd = obj["cwd"] as? String, !cwd.isEmpty { record.cwd = cwd }
        if record.pid == nil { record.pid = claudeAncestor() }

        if let out = try? encoder.encode(record) {
            try? out.write(to: file, options: .atomic)
        }
        exit(0)
    }

    /// Busca hacia arriba el proceso de Claude Code para saber luego si la sesión sigue viva.
    private static func claudeAncestor() -> Int32? {
        var pid = getppid()
        for _ in 0..<6 {
            guard pid > 1 else { return nil }
            if processPath(pid).lowercased().contains("claude") { return pid }
            // Instalado con npm, el ejecutable es node: mirar también sus argumentos.
            if let args = Power.run("/bin/ps", ["-p", String(pid), "-o", "args="]),
               AgentWatcher.agentName(args.trimmingCharacters(in: .whitespacesAndNewlines)) == "Claude Code" {
                return pid
            }
            guard let parent = parentPID(pid) else { return nil }
            pid = parent
        }
        return nil
    }

    private static func parentPID(_ pid: pid_t) -> pid_t? {
        var info = kinfo_proc()
        var size = MemoryLayout<kinfo_proc>.stride
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, pid]
        guard sysctl(&mib, 4, &info, &size, nil, 0) == 0, size > 0 else { return nil }
        return info.kp_eproc.e_ppid
    }

    private static func processPath(_ pid: pid_t) -> String {
        var buffer = [CChar](repeating: 0, count: 4096)
        guard proc_pidpath(pid, &buffer, UInt32(buffer.count)) > 0 else { return "" }
        return String(cString: buffer)
    }
}

// MARK: - Lectura desde la app

enum SessionStore {
    static func load(now: Date = Date()) -> [SessionRecord] {
        let fm = FileManager.default
        guard let files = try? fm.contentsOfDirectory(at: WickPaths.sessions, includingPropertiesForKeys: nil) else {
            return []
        }
        var result: [SessionRecord] = []
        for file in files where file.pathExtension == "json" {
            guard let data = try? Data(contentsOf: file),
                  var record = try? decoder.decode(SessionRecord.self, from: data) else { continue }
            let age = now.timeIntervalSince(record.updated)

            if let pid = record.pid, !isAlive(pid) {
                try? fm.removeItem(at: file)  // Claude Code se cerró sin SessionEnd
                continue
            }
            if record.pid == nil {
                if age > 24 * 3600 { try? fm.removeItem(at: file); continue }
                if age > 8 * 3600 { continue }
            }
            // Claude Code no avisa si lo interrumpes con Esc: sin eventos en 30 min, la sesión
            // se da por parada aunque el proceso siga abierto (si no, el Mac no dormiría nunca).
            if record.state != .idle && age > 30 * 60 { record.state = .idle }
            result.append(record)
        }
        return result  // la app las ordena junto con las de otros agentes
    }

    private static func isAlive(_ pid: Int32) -> Bool {
        kill(pid, 0) == 0 || errno == EPERM
    }
}
