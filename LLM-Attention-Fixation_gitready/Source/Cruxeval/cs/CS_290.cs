using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string prefix) {
        if (text.StartsWith(prefix))
        {
            return text.Remove(0, prefix.Length);
        }
        if (text.Contains(prefix))
        {
            return text.Replace(prefix, "").Trim();
        }
        return text.ToUpper();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abixaaaily"), ("al")).Equals(("ABIXAAAILY")));
    }

}
