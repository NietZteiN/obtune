using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string filename) {
        var suffix = filename.Split('.').Last();
        var f2 = filename + new string(suffix.Reverse().ToArray());
        return f2.EndsWith(suffix);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("docs.doc")) == (false));
    }

}
