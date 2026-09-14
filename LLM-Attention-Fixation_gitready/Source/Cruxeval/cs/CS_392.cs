using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        if (text.ToUpper() == text) {
            return "ALL UPPERCASE";
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Hello Is It MyClass")).Equals(("Hello Is It MyClass")));
    }

}
