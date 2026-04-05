# Security Checklist — simurgh-dns

## 1. DNS Packet Validation

- [ ] Validate packet minimum length (12 bytes for header) before parsing
- [ ] Check question count matches actual questions in packet
- [ ] Validate name compression pointers don't create loops
- [ ] Enforce maximum name length (253 characters, 63 per label)
- [ ] Reject packets with invalid opcode or rcode values
- [ ] Limit total packet size (512 bytes UDP standard, 4096 EDNS)
- [ ] Validate rdata length matches expected for record type

## 2. DNS-Specific Security

- [ ] Implement rate limiting per source IP to prevent amplification attacks
- [ ] Reject queries with spoofed source addresses when possible
- [ ] Validate response transaction IDs match query IDs
- [ ] Implement query name randomization for upstream queries (0x20 encoding)
- [ ] Set maximum TTL cap to prevent cache poisoning with long TTLs
- [ ] Log and alert on unusual query patterns (tunneling detection)
- [ ] Implement DNSSEC validation for upstream responses when configured

## 3. Path Validation

- [ ] Use `Path.resolve()` to canonicalize paths
- [ ] Prevent path traversal with `..` components
- [ ] Check file existence before operations
- [ ] Verify symlink targets are within allowed directories
- [ ] Never use string concatenation for paths — use `Path /` operator

## 4. Subprocess Safety

- [ ] Never use `shell=True` with user-provided input
- [ ] Use list form for subprocess arguments
- [ ] Set timeouts on all subprocess calls
- [ ] Validate CLI commands exist with `shutil.which()` before execution
- [ ] Capture and handle stderr
- [ ] Set `cwd` explicitly

## 5. Secret Management

- [ ] Never embed API keys or secrets in source code
- [ ] Use environment variables via `pydantic-settings`
- [ ] Never log secrets (mask in log output)
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Use separate configs for dev/staging/production

## 6. Network Security

- [ ] Validate upstream resolver addresses (no private ranges unless configured)
- [ ] Implement connection timeouts for all network operations
- [ ] Use TLS for DNS-over-TLS (DoT) when supported
- [ ] Bind to localhost by default — require explicit config for external binding
- [ ] Implement maximum concurrent connection limits

## 7. Input Validation

- [ ] Validate configuration values (port ranges, IP addresses, timeouts)
- [ ] Handle malformed YAML/JSON/TOML config gracefully
- [ ] Validate enum values against allowed sets
- [ ] Sanitize user input before logging
- [ ] Validate domain names against RFC 1035 label rules

## 8. Dependency Auditing

- [ ] Run security scanner on dependencies regularly
- [ ] Review new dependencies before adding
- [ ] Pin versions in `uv.lock`
- [ ] Monitor for CVEs in key dependencies
- [ ] Minimize dependency count — prefer stdlib when possible
