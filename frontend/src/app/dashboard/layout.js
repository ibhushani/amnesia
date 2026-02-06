import Sidebar from '@/components/Sidebar';

export default function DashboardLayout({ children }) {
    return (
        <div className="flex min-h-screen bg-[#050505] selection:bg-emerald-500/20">
            <Sidebar />
            <main className="flex-1 ml-72">
                <div className="max-w-[1600px] mx-auto p-8 lg:p-12">
                    {children}
                </div>
            </main>
        </div>
    );
}
