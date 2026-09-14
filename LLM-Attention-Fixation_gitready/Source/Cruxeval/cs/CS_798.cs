using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string pre) {
        if (!text.StartsWith(pre)) {
            return text;
        }
        return text.Remove(0, pre.Length);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("@hihu@!"), ("@hihu")).Equals(("@!")));
    }

}
