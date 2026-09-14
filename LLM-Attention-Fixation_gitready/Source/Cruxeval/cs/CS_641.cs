using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string number) {
        return long.TryParse(number, out _);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("dummy33;d")) == (false));
    }

}
