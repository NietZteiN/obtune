using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string w) {
        var ls = new List<char>(w.ToCharArray());
        var omw = "";
        while (ls.Count > 0)
        {
            omw += ls[0];
            ls.RemoveAt(0);
            if (ls.Count * 2 > w.Length)
            {
                if (w.Substring(ls.Count) == omw)
                {
                    return true;
                }
            }
        }
        return false;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("flak")) == (false));
    }

}
