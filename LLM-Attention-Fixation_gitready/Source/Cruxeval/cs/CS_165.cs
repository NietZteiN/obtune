using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text, long lower, long upper) {
        return text.Substring((int)lower, (int)(upper - lower)).All(char.IsLetterOrDigit);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("=xtanp|sugv?z"), (3L), (6L)) == (true));
    }

}
