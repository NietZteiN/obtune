using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long tabstop) {
        text = text.Replace("\n", "_____");
        text = text.Replace("\t", new string(' ', (int)tabstop));
        text = text.Replace("_____", "\n");
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("odes	code	well"), (2L)).Equals(("odes  code  well")));
    }

}
