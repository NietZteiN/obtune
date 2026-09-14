using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) {
        var l = new List<char>(str);
        for (int i = l.Count - 1; i >= 0; i--) {
            if (l[i] != ' ') {
                break;
            }
            l.RemoveAt(i);
        }
        return new string(l.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("    jcmfxv     ")).Equals(("    jcmfxv")));
    }

}
