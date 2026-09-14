using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        return text.Split(':')[0].Count(c => c == '#');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("#! : #!")) == (1L));
    }

}
