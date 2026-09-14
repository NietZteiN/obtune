using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text, string search) {
        return search.StartsWith(text);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("123"), ("123eenhas0")) == (true));
    }

}
