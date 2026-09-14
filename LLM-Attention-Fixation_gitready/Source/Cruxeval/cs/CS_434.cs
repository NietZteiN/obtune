using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string str) {
        try {
            return str.LastIndexOf('e');
        }
        catch (NullReferenceException) {
            return -1; // Return "-1" instead of "Nuk" in C#
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("eeuseeeoehasa")) == (8L));
    }

}
