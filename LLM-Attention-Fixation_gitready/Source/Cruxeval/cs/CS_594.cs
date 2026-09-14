using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string file) {
        return file.IndexOf('\n');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("n wez szize lnson tilebi it 504n.\n")) == (33L));
    }

}
