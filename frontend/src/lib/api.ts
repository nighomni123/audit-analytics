const API = "http://127.0.0.1:8788/api";
export async function get(path: string) { const r = await fetch(API+path); if (!r.ok) throw new Error(await r.text()); return r.json(); }
export async function post(path: string, body: any) { const r = await fetch(API+path, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)}); const d = await r.json(); if (!r.ok) throw new Error(d.error||r.statusText); return d; }
