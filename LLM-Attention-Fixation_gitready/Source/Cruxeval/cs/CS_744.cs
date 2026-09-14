using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string new_ending) {
        var result = new StringBuilder(text);
        result.Append(new_ending);
        return result.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("jro"), ("wdlp")).Equals(("jrowdlp")));
    }

}
