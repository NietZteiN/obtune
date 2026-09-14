using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string suffix) {
        if(suffix.StartsWith("/")) {
            return text + suffix.Substring(1);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hello.txt"), ("/")).Equals(("hello.txt")));
    }

}
