using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string st) {
        string swapped = "";
        foreach (char ch in st.Reverse())
        {
            swapped += char.IsUpper(ch) ? char.ToLower(ch) : char.ToUpper(ch);
        }
        return swapped;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("RTiGM")).Equals(("mgItr")));
    }

}
