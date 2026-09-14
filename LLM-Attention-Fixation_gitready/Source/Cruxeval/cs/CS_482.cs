using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        return text.Replace("\\\"", "\"");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Because it intrigues them")).Equals(("Because it intrigues them")));
    }

}
