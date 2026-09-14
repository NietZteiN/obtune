using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string delim) {
        string[] parts = text.Split(new string[] { delim }, StringSplitOptions.None);
        return parts[1] + delim + parts[0];
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("bpxa24fc5."), (".")).Equals((".bpxa24fc5")));
    }

}
