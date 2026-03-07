import { Mail, Lock, ArrowRight, Github } from 'lucide-react';
import { Link } from 'react-router-dom';
import { SiGoogle } from '@icons-pack/react-simple-icons';
const Login = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6">
      {/* Brand Header (matching your Sidebar) */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-900/40">
          <span className="text-white font-bold text-xl">S</span>
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-100">
          Sadaqa <span className="text-blue-400">Tech</span>
        </h2>
      </div>

      {/* Login Card */}
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <div className="mb-8">
          <h1 className="text-xl font-semibold text-white">Welcome back</h1>
          <p className="text-slate-400 text-sm mt-1">Please enter your details to sign in.</p>
        </div>

        <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
          {/* Email Field */}
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium text-slate-300 ml-1">
              Email Address
            </label>
            <div className="relative group">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
              <input 
                id="email"
                type="email" 
                required 
                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 transition-all" 
                placeholder="name@company.com"
              />
            </div>
          </div>

          {/* Password Field */}
          <div className="space-y-2">
            <div className="flex justify-between items-center ml-1">
              <label htmlFor="password" className="text-sm font-medium text-slate-300">
                Password
              </label>
              <a href="#" className="text-xs text-blue-400 hover:underline">Forgot?</a>
            </div>
            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
              <input 
                id="password"
                type="password" 
                required 
                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 transition-all" 
                placeholder="••••••••"
              />
            </div>
          </div>

          {/* Sign In Button */}
          <button 
            type="submit" 
            className="w-full hover:cursor-pointer bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 group shadow-lg shadow-blue-900/20 active:scale-[0.98]"
          >
            Sign In
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform " />
          </button>
        </form>

        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-slate-800"></span></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-slate-900 px-2 text-slate-500">Or continue with</span></div>
        </div>

        {/* Social Login Placeholder */}
        <button className="w-full bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 font-medium py-2.5 rounded-xl transition-all flex items-center justify-center gap-3">
          <Github className="w-5 h-5 hover:cursor-pointer" />
          GitHub
        </button>
        <button className="w-full bg-slate-950 border border-slate-800 hover:bg-slate-800 hover:cursor-pointer text-slate-300 font-medium py-2.5 rounded-xl transition-all flex items-center justify-center gap-3">
          <SiGoogle className="w-5 h-5" />
           Gmail account
         </button>

        <p className="text-center text-slate-500 text-sm mt-8">
          Don't have an account? <Link to="/signup" className="text-blue-400 hover:underline font-medium">Create one</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;