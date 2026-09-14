using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var new_text = text.Select(c => char.IsDigit(c) ? c : '*');
        return string.Join("", new_text);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("5f83u23saa")).Equals(("5*83*23***")));
    }

}
