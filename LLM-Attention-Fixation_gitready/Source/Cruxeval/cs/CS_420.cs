using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        try {
            return text.All(char.IsLetter);
        } catch {
            return false;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("x")) == (true));
    }

}
