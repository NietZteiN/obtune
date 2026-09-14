using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        if (!string.IsNullOrEmpty(text) && text == text.ToUpper())
        {
            var cs = text.ToUpper().Zip(text.ToLower(), (from, to) => (from, to))
                                .ToDictionary(pair => (int)pair.from, pair => pair.to);
            return string.Join("", text.Select(c => cs.ContainsKey((int)c) ? cs[(int)c] : c));
        }
        return text.ToLower().Substring(0, Math.Min(3, text.Length));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("mTYWLMwbLRVOqNEf.oLsYkZORKE[Ko[{n")).Equals(("mty")));
    }

}
