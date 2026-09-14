using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string txt, string sep, long sep_count) {
        string output = "";
        while (sep_count > 0 && txt.Count(s => s == sep[0]) > 0)
        {
            output += txt.Substring(0, txt.LastIndexOf(sep) + 1);
            txt = txt.Substring(txt.LastIndexOf(sep) + 1);
            sep_count--;
        }
        return output + txt;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("i like you"), (" "), (-1L)).Equals(("i like you")));
    }

}
