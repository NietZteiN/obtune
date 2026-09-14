using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string strand, string zmnc) {
        int poz = strand.IndexOf(zmnc);
        while (poz != -1)
        {
            strand = strand.Substring(poz + 1);
            poz = strand.IndexOf(zmnc);
        }
        return strand.LastIndexOf(zmnc);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((""), ("abc")) == (-1L));
    }

}
