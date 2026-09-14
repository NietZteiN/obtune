using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string postcode) {
        return postcode.Substring(postcode.IndexOf('C'));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ED20 CW")).Equals(("CW")));
    }

}
