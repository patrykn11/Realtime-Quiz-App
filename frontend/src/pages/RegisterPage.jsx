import { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { AuthContext } from "../components/LoginContext";

const inputClass = "w-full rounded-xl bg-white px-4 py-2 text-black";

export default function RegisterPage() {
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password_confirm: "",
  });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await register(form);
      navigate("/join");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full items-center justify-center px-4 py-10 text-white">
      <form className="flex w-full max-w-sm flex-col gap-5" onSubmit={handleSubmit}>
        <h1 className="text-center font-mono text-3xl">REGISTER</h1>
        <input
          className={inputClass}
          autoComplete="username"
          placeholder="username"
          value={form.username}
          onChange={(event) => setForm({ ...form, username: event.target.value })}
          required
        />
        <input
          className={inputClass}
          autoComplete="email"
          placeholder="email"
          type="email"
          value={form.email}
          onChange={(event) => setForm({ ...form, email: event.target.value })}
          required
        />
        <input
          className={inputClass}
          autoComplete="new-password"
          placeholder="password"
          type="password"
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
          required
        />
        <input
          className={inputClass}
          autoComplete="new-password"
          placeholder="confirm password"
          type="password"
          value={form.password_confirm}
          onChange={(event) => setForm({ ...form, password_confirm: event.target.value })}
          required
        />
        <button
          disabled={isSubmitting}
          className="rounded-xl px-4 py-2 font-mono hover:bg-white hover:text-black disabled:opacity-50"
        >
          {isSubmitting ? "Creating account..." : "Register"}
        </button>
        {error && <p role="alert" className="text-center text-red-200">{error}</p>}
        <p className="text-center text-sm">
          Already have an account?{" "}
          <Link className="underline" to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}
