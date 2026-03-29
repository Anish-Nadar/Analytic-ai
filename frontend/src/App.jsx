import { useState } from 'react'
import axios from 'axios'
import { UploadCloud, FileSpreadsheet, Loader2, CheckCircle, AlertCircle, Sparkles, Database, LayoutTemplate, TrendingUp, DollarSign, ShoppingCart, Lightbulb, ListOrdered, TrendingDown } from 'lucide-react'

function App() {
  const [file, setFile] = useState(null)
  
  // States
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null) // Phase 1
  
  const [cleaning, setCleaning] = useState(false)
  const [cleanResult, setCleanResult] = useState(null) // Phase 2
  
  const [computing, setComputing] = useState(false)
  const [metricsResult, setMetricsResult] = useState(null) // Phase 3

  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
      setError('')
      setResult(null)
      setCleanResult(null)
      setMetricsResult(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setError('')
    setCleanResult(null)
    setMetricsResult(null)
    try {
      const response = await axios.post('http://localhost:8000/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during upload.')
    } finally {
      setUploading(false)
    }
  }

  const handleClean = async () => {
    if (!result || !result.upload_id) return
    
    setCleaning(true)
    setError('')
    try {
      const response = await axios.post(`http://localhost:8000/clean/${result.upload_id}`)
      setCleanResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during cleaning.')
    } finally {
      setCleaning(false)
    }
  }

  const handleComputeMetrics = async () => {
    if (!result || !cleanResult) return
    
    setComputing(true)
    setError('')
    try {
      const response = await axios.post(`http://localhost:8000/metrics/${result.upload_id}`, {
        metadata_columns: cleanResult.detected_columns
      })
      setMetricsResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during metrics computation.')
    } finally {
      setComputing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header Block */}
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden flex flex-col items-center p-12 relative border border-gray-100">
          <div className="absolute top-0 w-full h-2 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
          
          <h1 className="text-4xl font-extrabold text-gray-900 mb-2 mt-4 tracking-tight text-center">
            AI Data Analyst <Sparkles className="inline text-yellow-500 mb-2" size={32}/>
          </h1>
          <p className="text-gray-500 mb-10 text-center text-lg max-w-xl">
            Upload your raw sales data and let AI clean, process, and extract actionable insights for your business.
          </p>

          <div className="group w-full max-w-2xl border-2 border-dashed border-gray-300 bg-gray-50/50 rounded-2xl p-12 flex flex-col items-center justify-center transition-all hover:bg-blue-50 hover:border-blue-400 hover:shadow-md cursor-pointer relative">
            <input 
              type="file" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
              accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
              onChange={handleFileChange}
            />
            <div className="bg-white p-4 rounded-full shadow-sm mb-4 group-hover:scale-110 transition-transform duration-300">
              <UploadCloud size={40} className="text-blue-500" />
            </div>
            <p className="text-xl font-semibold text-gray-700 mb-1">
              {file ? file.name : "Drag & Drop or Click to Upload"}
            </p>
            <p className="text-sm text-gray-500 text-center">Supported formats: CSV, Excel (XLSX, XLS)</p>
          </div>

          {error && (
            <div className="w-full max-w-2xl mt-6 p-4 bg-red-50 rounded-xl border border-red-200 flex items-center text-red-700">
              <AlertCircle className="mr-3 shrink-0" /> {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className={`mt-8 px-10 py-4 rounded-xl font-bold text-white text-lg transition-all shadow-lg flex items-center
              ${!file || uploading 
                ? 'bg-gray-400 cursor-not-allowed shadow-none' 
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-blue-500/30 transform hover:-translate-y-1'
              }`}
          >
            {uploading ? <><Loader2 className="animate-spin mr-3" size={24} /> Uploading...</> : <><FileSpreadsheet className="mr-3" size={24} /> Upload Data</>}
          </button>
        </div>

        {/* Phase 1: Upload Preview (Hidden if cleaned to save space) */}
        {result && !cleanResult && (
          <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100 animate-fade-in-up">
             <div className="flex justify-between flex-wrap gap-4 items-center border-b pb-6 mb-6">
               <div>
                  <h3 className="font-bold text-2xl text-gray-800 flex items-center"><Database className="mr-2 text-blue-500"/> Raw Data Preview</h3>
                  <p className="text-sm text-gray-500 mt-1">Upload exactly {result.filename}</p>
               </div>
               <button
                  onClick={handleClean}
                  disabled={cleaning}
                  className="px-6 py-3 rounded-lg font-bold text-white bg-purple-600 hover:bg-purple-700 transition shadow-md flex items-center"
               >
                 {cleaning ? <><Loader2 className="animate-spin mr-2"/> Cleaning...</> : <><Sparkles className="mr-2"/> Clean & Detect Columns</>}
               </button>
             </div>
             <div className="overflow-x-auto rounded-xl shadow-sm border border-gray-200">
                <table className="w-full text-left text-sm text-gray-600">
                  <thead className="bg-gray-100 text-gray-800 border-b border-gray-200">
                    <tr>{result.columns.map((col, idx) => <th key={idx} className="px-6 py-4 font-semibold whitespace-nowrap">{col}</th>)}</tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {result.preview.map((row, r_idx) => (
                      <tr key={r_idx} className="hover:bg-gray-50 transition-colors">
                        {result.columns.map((col, c_idx) => <td key={c_idx} className="px-6 py-3 whitespace-nowrap overflow-hidden text-ellipsis max-w-[200px]">{row[col] !== null ? String(row[col]) : ''}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
          </div>
        )}

        {/* Phase 2: Clean Result UI (Hidden if metrics calculated) */}
        {cleanResult && !metricsResult && (
          <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100 animate-fade-in-up">
            <div className="flex justify-between flex-wrap gap-4 items-center mb-6">
              <h3 className="font-bold text-2xl text-green-600 flex items-center"><CheckCircle className="mr-2" size={32}/> Data Configured!</h3>
              <button
                  onClick={handleComputeMetrics}
                  disabled={computing}
                  className="px-6 py-3 rounded-lg font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition shadow-lg flex items-center text-lg transform hover:-translate-y-1"
               >
                 {computing ? <><Loader2 className="animate-spin mr-2"/> Analyzing...</> : <><TrendingUp className="mr-2"/> Generate Dashboard</>}
               </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
               <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
                  <h4 className="font-bold text-blue-800 text-lg mb-4 flex items-center"><Sparkles className="mr-2" size={20}/> Correction Stats</h4>
                  <ul className="space-y-3 text-blue-900">
                     <li className="flex justify-between"><span>Initial Rows:</span> <span className="font-bold">{cleanResult.stats.initial_rows}</span></li>
                     <li className="flex justify-between"><span>Empty Rows Dropped:</span> <span className="font-bold text-red-500">{cleanResult.stats.rows_dropped}</span></li>
                     <li className="flex justify-between"><span>Duplicates Removed:</span> <span className="font-bold text-yellow-600">{cleanResult.stats.duplicates_removed}</span></li>
                     <li className="flex justify-between border-t border-blue-200 pt-2 mt-2"><span>Final Clean Rows:</span> <span className="font-bold text-xl">{cleanResult.stats.final_rows}</span></li>
                  </ul>
               </div>

               <div className="bg-purple-50 p-6 rounded-2xl border border-purple-100">
                  <h4 className="font-bold text-purple-800 text-lg mb-4 flex items-center"><LayoutTemplate className="mr-2" size={20}/> Detected Important Columns</h4>
                  <ul className="space-y-4 text-purple-900">
                     <li className="flex justify-between items-center"><span className="text-sm font-bold text-purple-600 uppercase">Date</span> <span className="font-medium bg-white px-3 py-1 rounded-md border border-purple-200 shadow-sm">{cleanResult.detected_columns.Date || 'No Date'}</span></li>
                     <li className="flex justify-between items-center"><span className="text-sm font-bold text-purple-600 uppercase">Revenue</span> <span className="font-medium bg-white px-3 py-1 rounded-md border border-purple-200 shadow-sm">{cleanResult.detected_columns.Revenue || 'No Revenue'}</span></li>
                     <li className="flex justify-between items-center"><span className="text-sm font-bold text-purple-600 uppercase">Product</span> <span className="font-medium bg-white px-3 py-1 rounded-md border border-purple-200 shadow-sm">{cleanResult.detected_columns.Product || 'No Product'}</span></li>
                  </ul>
               </div>
            </div>
          </div>
        )}

        {/* Phase 3: Metrics & Insights Dashboard */}
        {metricsResult && (
          <div className="animate-fade-in-up space-y-8">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 -mr-8 -mt-8 text-indigo-400/30"><DollarSign size={160}/></div>
                <div className="relative z-10">
                  <p className="font-medium text-indigo-100 mb-2 drop-shadow-sm flex items-center"><DollarSign size={18} className="mr-1"/> Total Revenue</p>
                  <h2 className="text-5xl font-black drop-shadow-md">
                    ${metricsResult.metrics.total_revenue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                  </h2>
                </div>
              </div>

              <div className="bg-gradient-to-br from-fuchsia-500 to-fuchsia-700 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 -mr-8 -mt-8 text-fuchsia-400/30"><ShoppingCart size={160}/></div>
                <div className="relative z-10">
                   <p className="font-medium text-fuchsia-100 mb-2 drop-shadow-sm flex items-center"><ShoppingCart size={18} className="mr-1"/> Total Orders</p>
                   <h2 className="text-5xl font-black drop-shadow-md">
                     {metricsResult.metrics.total_orders.toLocaleString()}
                   </h2>
                </div>
              </div>

              <div className="bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 -mr-8 -mt-8 text-emerald-400/30"><TrendingUp size={160}/></div>
                <div className="relative z-10">
                   <p className="font-medium text-emerald-100 mb-2 drop-shadow-sm flex items-center"><TrendingUp size={18} className="mr-1"/> Average Order Value</p>
                   <h2 className="text-5xl font-black drop-shadow-md">
                     ${metricsResult.metrics.aov.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                   </h2>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
               {/* Insights Panel */}
               <div className="lg:col-span-2 bg-white rounded-3xl shadow-xl border border-gray-100 p-8 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-yellow-100 rounded-full blur-3xl -mr-16 -mt-16"></div>
                  <h3 className="font-extrabold text-2xl text-gray-800 mb-6 flex items-center relative z-10"><Lightbulb className="mr-3 text-yellow-500" size={28}/> Key Business Insights</h3>
                  
                  <div className="space-y-4 relative z-10">
                    {metricsResult.insights.map((insight, idx) => (
                      <div key={idx} className="bg-gray-50/80 p-5 rounded-xl border border-gray-100 text-lg text-gray-700 leading-relaxed shadow-sm">
                        {insight}
                      </div>
                    ))}
                  </div>
               </div>

               {/* Top Products */}
               <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8">
                  <h3 className="font-extrabold text-2xl text-gray-800 mb-6 flex items-center"><TrendingUp className="mr-3 text-green-500" size={28}/> Top Performing</h3>
                  
                  <div className="space-y-4">
                     {metricsResult.top_products.length > 0 ? metricsResult.top_products.map((product, idx) => (
                       <div key={idx} className="flex justify-between items-center bg-green-50/50 p-4 rounded-xl border border-green-100">
                          <div className="flex items-center">
                            <span className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold text-sm mr-3 shadow-sm">{idx + 1}</span>
                            <span className="font-semibold text-gray-800 line-clamp-1 break-all pr-2">{product.name}</span>
                          </div>
                          {product.revenue > 0 ? (
                            <span className="font-bold text-green-700 bg-green-100 px-3 py-1 rounded-lg">${product.revenue.toLocaleString()}</span>
                          ) : (
                            <span className="font-bold text-green-700 bg-green-100 px-3 py-1 rounded-lg">{product.count} qty</span>
                          )}
                       </div>
                     )) : (
                       <div className="text-gray-500 italic text-center p-6 border-2 border-dashed rounded-xl">No products detected.</div>
                     )}
                  </div>
               </div>
               
               {/* Bottom Products */}
               <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8">
                  <h3 className="font-extrabold text-2xl text-gray-800 mb-6 flex items-center"><TrendingDown className="mr-3 text-red-500" size={28}/> Underperforming</h3>
                  
                  <div className="space-y-4">
                     {metricsResult.bottom_products?.length > 0 ? metricsResult.bottom_products.map((product, idx) => (
                       <div key={idx} className="flex justify-between items-center bg-red-50/50 p-4 rounded-xl border border-red-50">
                          <div className="flex items-center">
                            <span className="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center font-bold text-sm mr-3 shadow-sm">{idx + 1}</span>
                            <span className="font-semibold text-gray-800 line-clamp-1 break-all pr-2">{product.name}</span>
                          </div>
                          {product.revenue > 0 ? (
                            <span className="font-bold text-red-600 bg-red-100 px-3 py-1 rounded-lg">${product.revenue.toLocaleString()}</span>
                          ) : (
                            <span className="font-bold text-red-600 bg-red-100 px-3 py-1 rounded-lg">{product.count} qty</span>
                          )}
                       </div>
                     )) : (
                       <div className="text-gray-500 italic text-center p-6 border-2 border-dashed rounded-xl">No data available.</div>
                     )}
                  </div>
               </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default App
