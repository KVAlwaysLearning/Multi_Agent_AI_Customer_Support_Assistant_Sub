import { useState } from "react";
import { useRouter } from "next/router";
import { login } from "../services/api";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      const data = await login(email, password);
      localStorage.setItem("access_token", data.access_token);
      router.push("/");
    } catch (e) {
      setError("Invalid email or password.");
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-sm w-80 space-y-4">
        <h1 className="text-lg font-semibold text-gray-800">Log in</h1>
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
          Log in
        </button>
        <a href="/register" className="block text-xs text-center text-blue-600 hover:underline">
          Need an account? Register
        </a>
      </form>
    </div>
  );
}
