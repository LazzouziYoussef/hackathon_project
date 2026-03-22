import React from 'react';
import { Mail, Lock, User, ArrowRight, Github } from 'lucide-react';
import { Link } from 'react-router-dom';
import { SiGoogle } from '@icons-pack/react-simple-icons';

const SignIn = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6">
      {/* Brand Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-900/40">
          <span className="text-white font-bold text-xl">S</span>
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-100">
          Sadaqa <span className="text-blue-400">Tech</span>
        </h2>
      </div>

      {/* Sign In Card */}
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <div className="mb-8">
          <h1 className="text-xl font-semibold text-white">Create an account</h1>
          <p className="text-slate-400 text-sm mt-1">Join Sadaqa Tech to start monitoring.</p>
        </div>

        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
          {/* Full Name Field */}
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium text-slate-300 ml-1">
              Full Name
            </label>
            <div className="relative group">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
              <input 
                id="name"
                type="text" 
                required 
                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 transition-all" 
                placeholder="John Doe"
              />
            </div>
          </div>

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
            <label htmlFor="password" className="text-sm font-medium text-slate-300 ml-1">
              Password
            </label>
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

          {/* Submit Button */}
          <button 
            type="submit" 
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 mt-2 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 group shadow-lg shadow-blue-900/20 active:scale-[0.98]"
          >
            Create Account
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-slate-800"></span></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-slate-900 px-2 text-slate-500">Or sign up with</span></div>
        </div>

        {/* Social Options */}
        <div className="grid grid-cols-2 gap-4">
          <button className="bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 py-2.5 rounded-xl transition-all flex items-center justify-center gap-2">
            <SiGoogle size={18} />
            <span className="text-sm">Google</span>
          </button>
          <button className="bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 py-2.5 rounded-xl transition-all flex items-center justify-center gap-2">
            <Github size={18} />
            <span className="text-sm">GitHub</span>
          </button>
        </div>

        <p className="text-center text-slate-500 text-sm mt-8">
          Already have an account? <Link to="/login" className="text-blue-400 hover:underline font-medium">Log in</Link>
        </p>
      </div>
    </div>
  );
};

export default SignIn;