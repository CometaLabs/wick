import Foundation
import Darwin

/// Detecta agentes de terminal que no tienen hooks (Codex, Gemini CLI, Cursor Agent, Aider…)
/// mirando sus procesos: si el agente o lo que ha lanzado gasta CPU, está trabajando.
/// Claude Code se sigue por hooks, que es más preciso; solo se vigila por proceso si no están puestos.
final class AgentWatcher {
    /// Nombre del ejecutable (o del script de node/python) → nombre para mostrar.
    static let known: [String: String] = [
        "claude": "Claude Code",
        "codex": "Codex",
        "gemini": "Gemini CLI",
        "cursor-agent": "Cursor Agent",
        "opencode": "OpenCode",
        "aider": "Aider",
        "amp": "Amp",
        "goose": "Goose",
        "qwen": "Qwen Code",
        "crush": "Crush",
        "droid": "Factory Droid",
        "copilot": "Copilot CLI",
        "kiro-cli": "Kiro",
    ]

    /// CPU (suma del agente y sus descendientes) a partir de la cual cuenta como trabajando.
    private let busyCPU = 2.5
    /// Tras dejar de gastar CPU, sigue «trabajando» este rato (pausas entre llamadas al modelo).
    private let settle: TimeInterval = 25

    /// Lo que un agente lanzó hace más de esto (un servidor de desarrollo, un watcher) no cuenta:
    /// si no, un agente en pausa con un `npm run dev` abierto parecería trabajar siempre.
    private let maxChildAge: TimeInterval = 20 * 60

    private var lastBusy: [pid_t: Date] = [:]
    private var busySince: [pid_t: Date] = [:]
    private var firstSeen: [pid_t: Date] = [:]
    private(set) var sessions: [SessionRecord] = []
    private var running = false

    func refresh(includeClaude: Bool, completion: @escaping () -> Void) {
        guard !running else { return }
        running = true
        DispatchQueue.global(qos: .utility).async {
            let found = self.scan(includeClaude: includeClaude)
            DispatchQueue.main.async {
                self.sessions = found
                self.running = false
                completion()
            }
        }
    }

    private struct Proc {
        let pid: pid_t
        let ppid: pid_t
        let cpu: Double
        let age: TimeInterval
        let args: String
    }

    private func scan(includeClaude: Bool) -> [SessionRecord] {
        guard let out = Power.run("/bin/ps", ["-Axo", "pid=,ppid=,pcpu=,etime=,args="]) else { return [] }
        var procs: [Proc] = []
        for line in out.split(separator: "\n") {
            let parts = line.split(separator: " ", maxSplits: 4, omittingEmptySubsequences: true)
            guard parts.count == 5, let pid = pid_t(parts[0]), let ppid = pid_t(parts[1]),
                  let cpu = Double(parts[2].replacingOccurrences(of: ",", with: ".")) else { continue }
            procs.append(Proc(pid: pid, ppid: ppid, cpu: cpu, age: Self.seconds(etime: String(parts[3])),
                              args: String(parts[4])))
        }
        let children = Dictionary(grouping: procs, by: \.ppid)

        func treeCPU(_ pid: pid_t, depth: Int = 0) -> Double {
            guard depth < 8 else { return 0 }
            return (children[pid] ?? []).filter { $0.age < maxChildAge }
                .reduce(0) { $0 + $1.cpu + treeCPU($1.pid, depth: depth + 1) }
        }

        let now = Date()
        var agents: [(Proc, String)] = []
        let byPID = Dictionary(uniqueKeysWithValues: procs.map { ($0.pid, $0) })
        for p in procs {
            guard let name = Self.name(of: p), includeClaude || name != "Claude Code" else { continue }
            // Si el padre es el mismo agente (procesos auxiliares), cuenta solo el de arriba.
            if let parent = byPID[p.ppid], Self.name(of: parent) == name { continue }
            agents.append((p, name))
        }

        var result: [SessionRecord] = []
        var alive = Set<pid_t>()
        for (p, name) in agents {
            alive.insert(p.pid)
            let since = firstSeen[p.pid] ?? now
            firstSeen[p.pid] = since
            let cpu = p.cpu + treeCPU(p.pid)
            if cpu >= busyCPU { lastBusy[p.pid] = now }
            let busy = lastBusy[p.pid].map { now.timeIntervalSince($0) < settle } ?? false
            if busy { busySince[p.pid] = busySince[p.pid] ?? now } else { busySince[p.pid] = nil }
            result.append(SessionRecord(id: "proc-\(p.pid)", state: busy ? .working : .idle,
                                        cwd: Self.cwd(of: p.pid), pid: p.pid,
                                        since: busySince[p.pid] ?? lastBusy[p.pid] ?? since,
                                        updated: now, event: "process", agent: name))
        }
        lastBusy = lastBusy.filter { alive.contains($0.key) }
        firstSeen = firstSeen.filter { alive.contains($0.key) }
        busySince = busySince.filter { alive.contains($0.key) }
        return result
    }

    /// Nombre del agente de un proceso, o nil. Las apps de /Applications (Claude.app, Cursor.app…)
    /// no cuentan: son interfaces, no agentes de terminal.
    private static func name(of p: Proc) -> String? {
        let lower = p.args.lowercased()
        guard known.keys.contains(where: { lower.contains($0) }) else { return nil }  // filtro barato
        let path = executablePath(p.pid)
        if path.hasPrefix("/Applications/") || path.hasPrefix("/System/") { return nil }
        if let name = known[(path as NSString).lastPathComponent.lowercased()] { return name }
        return agentName(p.args)
    }

    /// Mira el ejecutable y, si es node/python/bun, el script que ejecuta.
    static func agentName(_ args: String) -> String? {
        let tokens = args.split(separator: " ").prefix(3).map(String.init)
        guard let first = tokens.first else { return nil }
        let exe = (first as NSString).lastPathComponent.lowercased()
        if let name = known[exe] { return name }
        let runtimes: Set<String> = ["node", "bun", "deno", "python", "python3"]
        guard runtimes.contains(exe) || exe.hasPrefix("python3.") else { return nil }
        for token in tokens.dropFirst() where !token.hasPrefix("-") {
            let script = ((token as NSString).lastPathComponent as NSString).deletingPathExtension.lowercased()
            if let name = known[script] { return name }
            // paquetes de npm: …/node_modules/@google/gemini-cli/…, …/@openai/codex/…
            for (key, name) in known where token.contains("/\(key)/") || token.contains("/\(key)-cli/") {
                return name
            }
            break
        }
        return nil
    }

    /// `etime` de ps: [[dd-]hh:]mm:ss
    static func seconds(etime: String) -> TimeInterval {
        var days = 0.0
        var rest = Substring(etime)
        if let dash = rest.firstIndex(of: "-") {
            days = Double(rest[..<dash]) ?? 0
            rest = rest[rest.index(after: dash)...]
        }
        let parts = rest.split(separator: ":").compactMap { Double($0) }
        return days * 86400 + parts.reduce(0) { $0 * 60 + $1 }
    }

    static func executablePath(_ pid: pid_t) -> String {
        var buffer = [CChar](repeating: 0, count: 4096)
        guard proc_pidpath(pid, &buffer, UInt32(buffer.count)) > 0 else { return "" }
        return String(cString: buffer)
    }

    static func cwd(of pid: pid_t) -> String? {
        var info = proc_vnodepathinfo()
        let size = Int32(MemoryLayout<proc_vnodepathinfo>.size)
        guard proc_pidinfo(pid, PROC_PIDVNODEPATHINFO, 0, &info, size) == size else { return nil }
        let path = withUnsafeBytes(of: info.pvi_cdir.vip_path) { raw in
            String(decoding: raw.prefix { $0 != 0 }, as: UTF8.self)
        }
        return path.isEmpty ? nil : path
    }
}
