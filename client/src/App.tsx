import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Header } from "./components/common/Header";
import { DashboardPage } from "./features/dashboard/DashboardPage";
import { ResumeListPage } from "./features/resumes/ResumeListPage";
import { ResumeDetailPage } from "./features/resumes/ResumeDetailPage";
import { JobListPage } from "./features/jobs/JobListPage";
import { JobDetailPage } from "./features/jobs/JobDetailPage";
import { EvaluationFlowPage } from "./features/evaluations/EvaluationFlowPage";
import { EvaluationResultPage } from "./features/evaluations/EvaluationResultPage";
import { EvaluationComparePage } from "./features/evaluations/EvaluationComparePage";
import { EvaluationHistoryPage } from "./features/evaluations/EvaluationHistoryPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30, // 30 seconds
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-background text-foreground selection:bg-primary/20">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/resumes" element={<ResumeListPage />} />
              <Route path="/resumes/:id" element={<ResumeDetailPage />} />
              <Route path="/jobs" element={<JobListPage />} />
              <Route path="/jobs/:id" element={<JobDetailPage />} />
              <Route path="/evaluate" element={<EvaluationFlowPage />} />
              <Route path="/evaluations/:id" element={<EvaluationResultPage />} />
              <Route path="/compare" element={<EvaluationComparePage />} />
              <Route path="/history" element={<EvaluationHistoryPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}