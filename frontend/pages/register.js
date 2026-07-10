import { useState } from "react";
import { useRouter } from "next/router";
import { register } from "../services/api";

export default function Register() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      const data = await register(email, password, name);
      localStorage.setItem("access_token", data.access_token);
      router.push("/");
    } catch (e) {
      setError("Could not register. Email may already be in use.");
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-sm w-80 space-y-4">
        <h1 className="text-lg font-semibold text-gray-800">Create account</h1>
        <input
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm"
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm"
          required
        />
        {error && <div className="text-xs text-red-600">{error}</div>}
        <button type="submit" className="w-full bg-blue-600 text-white rounded py-2 text-sm">
          Register
        </button>
        <a href="/login" className="block text-xs text-center text-blue-600 hover:underline">
          Already have an account? Log in
        </a>
      </form>
    </div>
  );
}
