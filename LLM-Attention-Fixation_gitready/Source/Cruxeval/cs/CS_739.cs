using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string st, List<string> pattern) {
        int index = 0;
        foreach (string p in pattern) {
            if (!st.StartsWith(p)) {
                return false;
            }
            st = st.Substring(p.Length);
            index += p.Length;
        }
        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("qwbnjrxs"), (new List<string>(new string[]{(string)"jr", (string)"b", (string)"r", (string)"qw"}))) == (false));
    }

}
