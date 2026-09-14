using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string a) {
        return string.Join(" ", a.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries));
    }
    public static void Main(string[] args) {
    Debug.Assert(F((" h e l l o   w o r l d! ")).Equals(("h e l l o w o r l d!")));
    }

}
