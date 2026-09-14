using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string sample) {
        int i = -1;
        while (sample.IndexOf('/', i+1) != -1)
        {
            i = sample.IndexOf('/', i+1);
        }
        return sample.Substring(0, i).LastIndexOf('/');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("present/here/car%2Fwe")) == (7L));
    }

}
