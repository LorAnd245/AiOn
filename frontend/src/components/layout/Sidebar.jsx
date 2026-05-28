import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Users, FolderKanban, Bot,
  MessageSquare, Settings, X, User, ChevronRight
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const adminItems = [
  { label: 'Dashboard',  icon: LayoutDashboard, path: '/dashboard',      accent: 'violet' },
  { label: 'Utenti',     icon: Users,           path: '/users',          accent: 'blue' },
  { label: 'Gruppi',     icon: FolderKanban,    path: '/groups',         accent: 'emerald' },
  { label: 'Agenti AI',  icon: Bot,             path: '/agents',         accent: 'orange' },
  { label: 'Chat',       icon: MessageSquare,   path: '/chat',           accent: 'cyan' },
];
const userItems = [
  { label: 'Dashboard',  icon: LayoutDashboard, path: '/user-dashboard', accent: 'violet' },
  { label: 'Chat AI',    icon: MessageSquare,   path: '/chat',           accent: 'cyan' },
];
const bottomItems = [
  { label: 'Profilo',      icon: User,     path: '/profile',  accent: 'pink' },
  { label: 'Impostazioni', icon: Settings, path: '/settings', accent: 'slate' },
];

const accentMap = {
  violet:  { bg: 'bg-violet-100 dark:bg-violet-500/15',  text: 'text-violet-600 dark:text-violet-400' },
  blue:    { bg: 'bg-blue-100 dark:bg-blue-500/15',      text: 'text-blue-600 dark:text-blue-400' },
  emerald: { bg: 'bg-emerald-100 dark:bg-emerald-500/15',text: 'text-emerald-600 dark:text-emerald-400' },
  orange:  { bg: 'bg-orange-100 dark:bg-orange-500/15',  text: 'text-orange-600 dark:text-orange-400' },
  cyan:    { bg: 'bg-cyan-100 dark:bg-cyan-500/15',      text: 'text-cyan-600 dark:text-cyan-400' },
  pink:    { bg: 'bg-pink-100 dark:bg-pink-500/15',      text: 'text-pink-600 dark:text-pink-400' },
  slate:   { bg: 'bg-slate-200 dark:bg-slate-500/15',    text: 'text-slate-600 dark:text-slate-400' },
};

function NavItem({ item, isActive, onClick }) {
  const a = accentMap[item.accent] || accentMap.slate;
  return (
    <Link
      to={item.path}
      onClick={onClick}
      className={`
        group flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-150
        ${isActive
          ? `${a.bg} ${a.text}`
          : 'text-slate-500 dark:text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5'
        }
      `}
    >
      <div className={`p-1.5 rounded-lg flex-shrink-0 transition-colors ${isActive ? a.text : 'text-slate-400 dark:text-slate-600'}`}>
        <item.icon size={15} />
      </div>
      <span className="text-sm font-medium flex-1">{item.label}</span>
      {isActive && <ChevronRight size={13} className={a.text + ' flex-shrink-0'} />}
    </Link>
  );
}

export default function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  const { isAdmin, user } = useAuth();
  const menuItems = isAdmin ? adminItems : userItems;
  const isActive = (path) => location.pathname === path;

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40" onClick={onClose} />

      <aside className="
        fixed top-0 left-0 h-full z-50 w-72
        bg-slate-50 dark:bg-[#0d1020]
        border-r border-slate-200 dark:border-white/5
        shadow-2xl shadow-black/10 dark:shadow-black/50
        flex flex-col animate-slide-right
      ">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-white/5">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="AION" className="w-8 h-8 object-contain" />
            <div>
              <span className="font-black gradient-text text-lg tracking-tight">AION</span>
              <p className="text-[10px] text-slate-400 dark:text-slate-600 -mt-0.5 tracking-widest uppercase">Enterprise</p>
            </div>
          </div>
          <button onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors">
            <X size={17} />
          </button>
        </div>

        {/* User pill */}
        <div className="px-4 py-3 border-b border-slate-200 dark:border-white/5">
          <div className="flex items-center gap-3 px-3 py-2.5
            bg-slate-100 dark:bg-[#11131d]
            border border-slate-200 dark:border-white/5 rounded-xl">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
              style={{ backgroundColor: user?.avatar_color || '#7c3aed' }}
            >
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">
                {user?.full_name || user?.username}
              </p>
              <p className="text-[10px] text-slate-500 dark:text-slate-600">{isAdmin ? '👑 Admin' : '👤 Utente'}</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-5">
          <div>
            <p className="text-[10px] font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest mb-2 px-2">
              Navigazione
            </p>
            <div className="space-y-0.5">
              {menuItems.map(item => (
                <NavItem key={item.path} item={item} isActive={isActive(item.path)} onClick={onClose} />
              ))}
            </div>
          </div>

          <div>
            <p className="text-[10px] font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest mb-2 px-2">
              Account
            </p>
            <div className="space-y-0.5">
              {bottomItems.map(item => (
                <NavItem key={item.path} item={item} isActive={isActive(item.path)} onClick={onClose} />
              ))}
            </div>
          </div>
        </nav>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-slate-200 dark:border-white/5 flex items-center justify-between">
          <span className="text-xs text-slate-400 dark:text-slate-700">AION Platform</span>
          <span className="text-xs px-2 py-0.5
            bg-violet-100 dark:bg-violet-500/10
            text-violet-600 dark:text-violet-400
            border border-violet-200 dark:border-violet-500/20 rounded-full">
            v2.0.0
          </span>
        </div>
      </aside>
    </>
  );
}
