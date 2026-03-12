import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileText, Briefcase, Building2, ChevronRight, CheckCircle2, XCircle } from 'lucide-react';
import axios from 'axios';

const LoadingState = ({ messages }) => {
  const [msgIndex, setMsgIndex] = useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex((prev) => (prev + 1) % messages.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [messages.length]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex flex-col items-center justify-center p-16 space-y-6 text-center"
    >
      <div className="relative w-24 h-24">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 border-4 border-t-[#38bdf8] border-r-transparent border-b-[#22c55e] border-l-transparent rounded-full"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          className="absolute inset-2 border-4 border-t-transparent border-r-[#8b5cf6] border-b-transparent border-l-[#ec4899] rounded-full opacity-70"
        />
      </div>
      <motion.p
        key={msgIndex}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="text-xl font-bold text-slate-700"
      >
        {messages[msgIndex]}
      </motion.p>
    </motion.div>
  );
};

export default function Home() {
  const [stage, setStage] = useState('input');
  const [inputType, setInputType] = useState('upload');
  const [resumeText, setResumeText] = useState('');
  const [uploadFile, setUploadFile] = useState(null);
  const [targetRole, setTargetRole] = useState('');
  const [company, setCompany] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const loadingMessages = [
    "Analyzing Resume Structure...",
    "Extracting Technical Skills...",
    "Fetching Job Requirements...",
    "Computing Skill Gap...",
    "Generating Personality Profile...",
    "Finalizing Analytics Dashboard..."
  ];

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploadFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError('');

    if (inputType === 'paste' && !resumeText.trim()) {
      setError("Please paste your resume text.");
      return;
    }
    if (inputType === 'upload' && !uploadFile) {
      setError("Please select a file to upload.");
      return;
    }
    if (!targetRole.trim()) {
      setError("Please specify a Target Job Position.");
      return;
    }

    setStage('loading');

    try {
      let resp;
      if (inputType === 'upload') {
        const formData = new FormData();
        formData.append('file', uploadFile);
        formData.append('targetRole', targetRole);
        formData.append('company', company);
        resp = await axios.post('/api/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else {
        resp = await axios.post('/api/analyze', {
          inputType: 'text',
          value: resumeText,
          targetRole,
          company
        });
      }

      if (resp.data.error) {
        throw new Error(resp.data.error);
      }
      setResult(resp.data);
      setStage('result');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Analysis failed. Please try again.');
      setStage('input');
    }
  };

  const reset = () => {
    setStage('input');
    setResult(null);
    setError('');
  };

  return (
    <div className="w-full min-h-screen bg-slate-50/50 text-slate-800 font-sans tracking-wide selection:bg-sky-500/30 overflow-x-hidden">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white/70 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col md:flex-row items-center justify-between text-center gap-4">
          <div className="flex items-center space-x-3 mx-auto md:mx-0 cursor-pointer transition-transform hover:scale-105">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-sky-500/20">
               <svg fill="currentColor" viewBox="0 0 24 24" className="w-6 h-6 text-white"><path d="M19 4h-1V3c0-.55-.45-1-1-1s-1 .45-1 1v1h-1c-.55 0-1 .45-1 1s.45 1 1 1h1v1c0 .55.45 1 1 1s1-.45 1-1V6h1c.55 0 1-.45 1-1s-.45-1-1-1zM9.54 9.11l-1.96-4.5c-.32-.73-1.35-.73-1.67 0l-1.96 4.5-4.5 1.96c-.73.32-.73 1.35 0 1.67l4.5 1.96 1.96 4.5c.32.73 1.35.73 1.67 0l1.96-4.5 4.5-1.96c.73-.32.73-1.35 0-1.67l-4.5-1.96zM8.7 12.3l-.7.7-.7-.7c-.39-.39-1.02-.39-1.41 0s-.39 1.02 0 1.41l.7.7-.7.7c-.39.39-.39 1.02 0 1.41s1.02.39 1.41 0l.7-.7.7.7c.39.39 1.02.39 1.41 0s.39-1.02 0-1.41l-.7-.7.7-.7c.39-.39.39-1.02 0-1.41s-1.02-.39-1.41 0zm10.3 5.7h-1v-1c0-.55-.45-1-1-1s-1 .45-1 1v1h-1c-.55 0-1 .45-1 1s.45 1 1 1h1v1c0 .55.45 1 1 1s1-.45 1-1v-1h1c.55 0 1-.45 1-1s-.45-1-1-1z"/></svg>
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-sky-600 to-indigo-600">
              Resume Intelligence
            </h1>
          </div>
          {stage === 'result' && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={reset}
              className="text-sm font-bold text-sky-600 hover:text-sky-700 transition-colors bg-sky-50 hover:bg-sky-100 px-6 py-2.5 rounded-full border border-sky-100 shadow-sm"
            >
              Start New Analysis
            </motion.button>
          )}
        </div>
      </header>

      <main className="w-full max-w-7xl mx-auto px-6 py-12 flex flex-col items-center justify-center">
        <AnimatePresence mode="wait">
          
          {/* STAGE: INPUT */}
          {stage === 'input' && (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-3xl mx-auto text-center"
            >
              <div className="mb-10">
                <h2 className="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight text-slate-800">AI Resume <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 to-indigo-500">Analytics</span></h2>
                <p className="text-lg text-slate-500 font-medium">Map your skills, discover gaps, and generate your career roadmap in seconds.</p>
              </div>

              <motion.form 
                onSubmit={handleAnalyze} 
                className="relative rounded-[2rem] p-10 space-y-10 bg-white shadow-xl max-w-2xl mx-auto"
                initial={{ boxShadow: "0 10px 15px -3px rgba(0,0,0,0.05)" }}
                animate={{ 
                  boxShadow: ["0 10px 15px -3px rgba(0,0,0,0.05)", "0 20px 40px -5px rgba(56,189,248,0.2)", "0 10px 15px -3px rgba(0,0,0,0.05)"],
                  border: ['1px solid rgba(226,232,240,1)', '1px solid rgba(56,189,248,0.5)', '1px solid rgba(226,232,240,1)']
                }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              >
                {/* Error Banner */}
                {error && (
                  <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start space-x-3 text-red-600 text-left text-sm font-medium">
                    <XCircle className="w-5 h-5 shrink-0 mt-0.5" />
                    <span>{error}</span>
                  </motion.div>
                )}

                {/* Section 1: Resume */}
                <div className="space-y-6 text-left">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2 justify-center">
                    <span className="w-7 h-7 rounded-full border border-slate-300 flex items-center justify-center text-xs text-sky-500 bg-sky-50 font-black">1</span>
                    Provide Resume
                  </h3>
                  
                  <div className="flex bg-slate-100/50 p-1.5 rounded-xl border border-slate-200">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      type="button"
                      className={`flex-1 py-3 text-sm font-bold rounded-lg transition-all ${inputType === 'upload' ? 'bg-white text-sky-600 shadow-sm border border-slate-200/60' : 'text-slate-500 hover:text-slate-700'}`}
                      onClick={() => setInputType('upload')}
                    >
                      Upload File
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      type="button"
                      className={`flex-1 py-3 text-sm font-bold rounded-lg transition-all ${inputType === 'paste' ? 'bg-white text-sky-600 shadow-sm border border-slate-200/60' : 'text-slate-500 hover:text-slate-700'}`}
                      onClick={() => setInputType('paste')}
                    >
                      Paste Text
                    </motion.button>
                  </div>

                  {inputType === 'upload' ? (
                    <label className="border-2 border-dashed hover:border-sky-400 border-slate-200 bg-slate-50 hover:bg-sky-50 transition-all rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer group shadow-sm">
                      <div className="w-16 h-16 mb-4 rounded-full bg-white border border-slate-100 flex items-center justify-center group-hover:scale-110 transition-transform shadow-md shadow-sky-500/10">
                        <UploadCloud className="w-8 h-8 text-sky-500" />
                      </div>
                      <p className="font-bold text-slate-700 mb-1">{uploadFile ? uploadFile.name : 'Click to select resume file'}</p>
                      <p className="text-sm text-slate-400 font-medium">PDF, TXT, or DOCX</p>
                      <input type="file" accept=".pdf,.txt,.docx" onChange={handleFileChange} className="hidden" />
                    </label>
                  ) : (
                    <textarea
                      className="w-full h-48 bg-slate-50 border border-slate-200 rounded-2xl p-5 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:bg-white transition-all shadow-inner resize-y text-sm font-medium"
                      placeholder="Paste your full resume text here..."
                      value={resumeText}
                      onChange={(e) => setResumeText(e.target.value)}
                    />
                  )}
                </div>

                {/* Section 2: Target */}
                <div className="space-y-6 pt-6 border-t border-slate-100 text-left">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2 justify-center">
                    <span className="w-7 h-7 rounded-full border border-slate-300 flex items-center justify-center text-xs text-sky-500 bg-sky-50 font-black">2</span>
                    Target Position
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs text-slate-600 font-bold ml-1 flex items-center justify-center gap-2 uppercase tracking-wider">
                        <Briefcase className="w-4 h-4 text-sky-500" /> Role Name <span className="text-sky-500">*</span>
                      </label>
                      <input
                        type="text"
                        className="w-full text-center bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-slate-800 placeholder-slate-400 font-bold focus:outline-none focus:ring-2 focus:ring-sky-400 focus:bg-white transition-all"
                        placeholder="e.g. AI Engineer"
                        value={targetRole}
                        onChange={(e) => setTargetRole(e.target.value)}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs text-slate-600 font-bold ml-1 flex items-center justify-center gap-2 uppercase tracking-wider">
                        <Building2 className="w-4 h-4 text-sky-500" /> Company <span className="text-slate-400 tracking-normal capitalize">(Optional)</span>
                      </label>
                      <input
                        type="text"
                        className="w-full text-center bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-slate-800 placeholder-slate-400 font-bold focus:outline-none focus:ring-2 focus:ring-sky-400 focus:bg-white transition-all"
                        placeholder="e.g. Google"
                        value={company}
                        onChange={(e) => setCompany(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                <div className="pt-4">
                  <motion.button
                    whileHover={{ scale: 1.02, backgroundColor: "rgb(2 132 199)" }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    className="w-full py-4.5 bg-gradient-to-r from-sky-500 to-indigo-500 rounded-xl font-black text-lg text-white shadow-xl shadow-sky-500/30 flex items-center justify-center gap-3 group"
                  >
                    Analyze Resume <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                  </motion.button>
                </div>
              </motion.form>
            </motion.div>
          )}

          {/* STAGE: LOADING */}
          {stage === 'loading' && (
            <motion.div key="loading" className="flex justify-center items-center min-h-[60vh]">
              <LoadingState messages={loadingMessages} />
            </motion.div>
          )}

          {/* STAGE: RESULT DASHBOARD */}
          {stage === 'result' && result && (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-10"
            >
              <div className="text-center mb-8">
                <h2 className="text-3xl font-extrabold text-slate-800">Your Intelligence <span className="text-sky-500">Analytics Report</span></h2>
                <p className="text-slate-500 font-medium mt-2">Data-driven insights tailored exactly to your objective.</p>
              </div>

              {/* Top Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                 {/* Score Card */}
                 <motion.div whileHover={{ y: -5 }} className="glass-panel p-8 rounded-[2rem] relative overflow-hidden group border-slate-200 text-center flex flex-col items-center justify-center">
                   <div className="absolute -top-4 -right-4 p-4 opacity-5 pointer-events-none">
                       <FileText className="w-32 h-32 text-indigo-500" />
                   </div>
                   <h3 className="text-slate-500 font-bold uppercase tracking-widest text-xs mb-3">Suitability Score</h3>
                   <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-indigo-500 to-sky-500 mb-2">{(result.score * 100).toFixed(0)}<span className="text-2xl text-slate-300 font-bold">/100</span></div>
                   <div className="w-full bg-slate-100 rounded-full h-3 mt-4 border border-slate-200">
                     <motion.div 
                        initial={{ width: 0 }} animate={{ width: `${result.score * 100}%` }} transition={{ duration: 1.5, ease: "easeOut" }}
                        className="bg-gradient-to-r from-indigo-400 to-sky-400 h-full rounded-full"
                     ></motion.div>
                   </div>
                 </motion.div>

                 {/* Role Info */}
                 <motion.div whileHover={{ y: -5 }} className="glass-panel p-8 rounded-[2rem] md:col-span-2 flex flex-col justify-center text-center">
                    <p className="text-slate-500 font-bold uppercase tracking-widest text-xs mb-3">Target Objective</p>
                    <h2 className="text-4xl md:text-5xl font-black text-slate-800 tracking-tight">
                      {targetRole} {company ? <span className="text-sky-500">@ {company}</span> : ''}
                    </h2>
                    <p className="text-slate-500 font-medium mt-4 bg-slate-100 py-2 px-6 rounded-full inline-block mx-auto">Analysis generated against {(result.role_skills || []).length} baseline skills.</p>
                 </motion.div>
              </div>

              {/* Main Analytics Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                
                {/* Left Column: Skills & Gap Analysis (7 cols) */}
                <div className="lg:col-span-7 space-y-10">
                  
                  <motion.div whileHover={{ boxShadow: "0 25px 50px -12px rgba(0,0,0,0.1)" }} className="glass-panel p-8 rounded-[2rem] transition-all text-center">
                    <h3 className="text-2xl font-black mb-8 flex items-center justify-center gap-3"><CheckCircle2 className="text-emerald-500 w-8 h-8"/> Match Analysis</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                      <div>
                        <h4 className="text-xs font-bold text-emerald-600 uppercase tracking-widest mb-6 border-b border-emerald-100 pb-3">Matching Skills ({result.matching_skills?.length || 0})</h4>
                        <div className="flex flex-wrap gap-2 justify-center">
                           {result.matching_skills && result.matching_skills.length > 0 ? (
                             result.matching_skills.map((skill, i) => (
                               <motion.span whileHover={{ scale: 1.1 }} key={i} className="px-4 py-1.5 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-full text-xs font-bold uppercase tracking-wider shadow-sm">
                                 {skill}
                               </motion.span>
                             ))
                           ) : (
                             <p className="text-slate-400 text-sm font-medium italic">No exact matches found.</p>
                           )}
                        </div>
                      </div>
                      
                      <div>
                         <h4 className="text-xs font-bold text-orange-600 uppercase tracking-widest mb-6 border-b border-orange-100 pb-3">Missing To Learn ({result.missing_skills?.length || 0})</h4>
                         <div className="flex flex-wrap gap-2 justify-center">
                           {result.missing_skills && result.missing_skills.length > 0 ? (
                             result.missing_skills.map((skill, i) => (
                               <motion.span whileHover={{ scale: 1.1 }} key={i} className="px-4 py-1.5 bg-orange-50 border border-orange-200 text-orange-700 rounded-full text-xs font-bold uppercase tracking-wider shadow-sm">
                                 {skill}
                               </motion.span>
                             ))
                           ) : (
                              <p className="text-slate-400 text-sm font-medium italic">You have all core requirements!</p>
                           )}
                         </div>
                      </div>
                    </div>
                  </motion.div>

                  {/* Competency Profile Bar Chart Component */}
                  <motion.div whileHover={{ boxShadow: "0 25px 50px -12px rgba(0,0,0,0.1)" }} className="glass-panel p-8 rounded-[2rem] transition-all">
                     <h3 className="text-2xl font-black mb-8 text-center text-slate-800">Competency Profile</h3>
                     <div className="space-y-6">
                       {result.personality && Object.entries(result.personality).map(([trait, score], idx) => (
                          <div key={idx} className="group">
                             <div className="flex justify-between mb-2 px-1">
                               <span className="text-sm font-bold text-slate-600 uppercase tracking-wider">{trait}</span>
                               <span className="text-sm font-black text-sky-500">{score.toFixed(1)}/10</span>
                             </div>
                             <div className="w-full bg-slate-100 rounded-full h-3 border border-slate-200">
                                <motion.div 
                                  initial={{ width: 0 }} animate={{ width: `${score * 10}%` }} transition={{ duration: 1 }}
                                  className="bg-sky-400 h-full rounded-full shadow-inner group-hover:bg-sky-500 transition-colors"
                                ></motion.div>
                             </div>
                          </div>
                       ))}
                     </div>
                  </motion.div>

                </div>

                 {/* Right Column: Visual Charts (5 cols) */}
                <div className="lg:col-span-5 space-y-10">
                  {/* Probability Tracker */}
                  <motion.div whileHover={{ y: -5 }} className="glass-panel p-10 rounded-[2rem] flex flex-col items-center justify-center text-center">
                    <h3 className="text-xl font-black mb-6 text-slate-800 uppercase tracking-widest">Interview Probability</h3>
                    <div className="relative w-56 h-56 flex items-center justify-center mb-6">
                       <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                         <circle className="text-slate-100 stroke-current" strokeWidth="8" cx="50" cy="50" r="40" fill="transparent"></circle>
                         <motion.circle 
                            className={`${result.probability >= 50 ? 'text-emerald-500' : 'text-amber-500'} stroke-current`} 
                            strokeWidth="8" 
                            strokeLinecap="round" 
                            cx="50" cy="50" r="40" fill="transparent" 
                            strokeDasharray="251.2" 
                            initial={{ strokeDashoffset: 251.2 }}
                            animate={{ strokeDashoffset: 251.2 - (251.2 * result.probability) / 100 }}
                            transition={{ duration: 2, ease: "easeOut" }}
                         ></motion.circle>
                       </svg>
                       <div className="absolute flex flex-col items-center">
                          <span className="text-6xl font-black text-slate-800">{result.probability}%</span>
                       </div>
                    </div>
                    <p className={`font-black uppercase tracking-widest text-lg py-2 px-6 rounded-full ${result.probability >= 50 ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}`}>{result.probability_tier}</p>
                  </motion.div>

                  {/* Charts */}
                  <motion.div whileHover={{ scale: 1.02 }} className="glass-panel p-6 rounded-[2rem] group bg-white text-center">
                     <h4 className="font-bold text-slate-500 mb-6 border-b border-slate-100 pb-3 uppercase tracking-widest text-sm">Skill Domain Coverage</h4>
                     <img 
                       src={`${result.radar_chart}?t=${new Date().getTime()}`} 
                       alt="Skill Radar Chart" 
                       className="w-full h-auto drop-shadow-xl rounded-2xl mx-auto mix-blend-multiply"
                     />
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.02 }} className="glass-panel p-6 rounded-[2rem] group bg-white text-center">
                     <h4 className="font-bold text-slate-500 mb-6 border-b border-slate-100 pb-3 uppercase tracking-widest text-sm">Behavioral Graph</h4>
                     <img 
                       src={`${result.spider_chart}?t=${new Date().getTime()}`} 
                       alt="Personality Spider Chart" 
                       className="w-full h-auto drop-shadow-xl rounded-2xl mx-auto mix-blend-multiply"
                     />
                  </motion.div>
                </div>
              </div>


              {/* Learning Roadmap */}
              {result.roadmap && Object.keys(result.roadmap).length > 0 && (
                <div className="glass-panel p-10 rounded-[2rem] mt-12 bg-white text-center">
                  <h3 className="text-3xl font-black mb-10 text-slate-800">Your Actionable Career Roadmap</h3>
                  <div className="relative border-l-2 border-slate-200 ml-4 md:ml-8 space-y-16 text-left">
                     {Object.entries(result.roadmap).map(([week, details], idx) => (
                        <div key={idx} className="relative pl-10 md:pl-16">
                           <div className="absolute w-8 h-8 bg-sky-500 rounded-full -left-[17px] top-1 ring-8 ring-white shadow-lg shadow-sky-500/30 flex items-center justify-center">
                             <div className="w-3 h-3 bg-white rounded-full"></div>
                           </div>
                           <h4 className="text-2xl font-black text-sky-600 mb-6">{week}</h4>
                           <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                              <motion.div whileHover={{ y: -5 }} className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-sky-300 transition-colors shadow-sm text-center">
                                <p className="text-xs text-sky-600 uppercase font-black tracking-widest mb-3">Topics</p>
                                <p className="text-sm font-bold text-slate-700">{details.topics}</p>
                              </motion.div>
                              <motion.div whileHover={{ y: -5 }} className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-emerald-300 transition-colors shadow-sm text-center">
                                <p className="text-xs text-emerald-600 uppercase font-black tracking-widest mb-3">Practice</p>
                                <p className="text-sm font-bold text-slate-700">{details.practice}</p>
                              </motion.div>
                              <motion.div whileHover={{ y: -5 }} className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-indigo-300 transition-colors shadow-sm text-center">
                                <p className="text-xs text-indigo-600 uppercase font-black tracking-widest mb-3">Project</p>
                                <p className="text-sm font-bold text-slate-700">{details.project}</p>
                              </motion.div>
                           </div>
                        </div>
                     ))}
                  </div>
                </div>
              )}

              {/* Improvements & Questions Grid */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-10 mt-12">
                 {/* Improvements */}
                 <div className="glass-panel p-10 rounded-[2rem] text-center">
                   <h3 className="text-2xl font-black mb-8 text-slate-800">Improvement Suggestions</h3>
                   <ul className="space-y-4 text-left">
                     {result.improvements && result.improvements.map((imp, idx) => (
                       <motion.li whileHover={{ x: 5 }} key={idx} className="flex items-start gap-4 bg-slate-50 p-5 rounded-2xl border border-slate-200 shadow-sm transition-all hover:bg-white text-center md:text-left mx-auto">
                         <div className="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0 mt-2.5 shadow-sm shadow-emerald-500/50"></div>
                         <p className="text-slate-700 text-sm font-bold leading-relaxed">{imp}</p>
                       </motion.li>
                     ))}
                   </ul>
                 </div>

                 {/* Questions */}
                 <div className="glass-panel p-10 rounded-[2rem] text-center">
                   <h3 className="text-2xl font-black mb-8 text-slate-800">Expected Interview Questions</h3>
                   <div className="space-y-8">
                     {result.questions && (() => {
                        const grouped = {};
                        result.questions.forEach(q => {
                           if(!grouped[q.type]) grouped[q.type] = [];
                           grouped[q.type].push(q.question);
                        });
                        return Object.entries(grouped).map(([type, qs], idx) => (
                           <div key={idx} className="bg-slate-50 p-6 rounded-2xl border border-slate-200">
                              <h4 className="text-xs font-black text-sky-600 uppercase tracking-widest mb-4 pb-3 border-b border-slate-200">{type}</h4>
                              <ul className="space-y-4 text-left">
                                {qs.map((q, q_idx) => (
                                  <li key={q_idx} className="text-sm font-bold text-slate-700 pl-4 border-l-4 border-sky-200">{q}</li>
                                ))}
                              </ul>
                           </div>
                        ));
                     })()}
                   </div>
                 </div>
              </div>

            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
