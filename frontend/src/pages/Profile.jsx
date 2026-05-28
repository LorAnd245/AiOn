import { User, Mail, Shield, Crown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';

export default function Profile() {
  const { user, isAdmin } = useAuth();

  return (
    <DashboardLayout>
      <div className="mb-7">
        <h1 className="text-xl font-bold text-slate-900 dark:text-white mb-0.5">Profilo</h1>
        <p className="text-slate-500 dark:text-slate-500 text-sm">Le tue informazioni personali</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Avatar card */}
        <div className="bg-white dark:bg-[#13162a] border border-slate-200 dark:border-white/5 rounded-2xl p-6 text-center">
          <div
            className="w-20 h-20 rounded-2xl flex items-center justify-center text-white text-3xl font-bold mx-auto mb-4 shadow-lg"
            style={{ backgroundColor: user?.avatar_color || '#7c3aed' }}
          >
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <h2 className="font-bold text-slate-900 dark:text-white mb-0.5">{user?.full_name || user?.username}</h2>
          <p className="text-slate-500 dark:text-slate-600 text-xs mb-4">{user?.email}</p>
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${
            user?.role === 'admin'
              ? 'bg-violet-100 dark:bg-violet-500/10 text-violet-600 dark:text-violet-400 border-violet-200 dark:border-violet-500/20'
              : 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-500 border-slate-200 dark:border-white/10'
          }`}>
            {user?.role === 'admin' ? <Crown size={12} /> : <User size={12} />}
            {user?.role === 'admin' ? 'Amministratore' : 'Utente'}
          </span>
        </div>

        {/* Info */}
        <div className="lg:col-span-2 bg-white dark:bg-[#13162a] border border-slate-200 dark:border-white/5 rounded-2xl p-6">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-5">Informazioni Account</h3>
          <div className="space-y-3">
            {[
              { label: 'Username', value: user?.username, icon: User },
              { label: 'Email', value: user?.email, icon: Mail },
              { label: 'Ruolo', value: user?.role === 'admin' ? 'Amministratore' : 'Utente Standard', icon: Shield },
            ].map(({ label, value, icon: Icon }) => (
              <div key={label} className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-[#11131d] rounded-xl border border-slate-200 dark:border-white/5">
                <div className="p-2.5 bg-violet-100 dark:bg-violet-500/10 rounded-xl">
                  <Icon size={16} className="text-violet-600 dark:text-violet-400" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-600 mb-0.5">{label}</p>
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{value}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-5 p-4 bg-cyan-50 dark:bg-cyan-500/5 border border-cyan-200 dark:border-cyan-500/15 rounded-xl">
            <p className="text-xs text-cyan-600 dark:text-cyan-400">
              💡 {isAdmin ? 'Per modificare le tue informazioni, contatta un nostro gestore.' : 'Per modificare le tue informazioni, contatta un amministratore.'}
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
