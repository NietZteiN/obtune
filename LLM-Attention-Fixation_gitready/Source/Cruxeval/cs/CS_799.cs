using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string st) {
        if (st[0] == '~')
        {
            string e = st.PadLeft(10, 's');
            return F(e);
        }
        else
        {
            return st.PadLeft(10, 'n');
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("eqe-;ew22")).Equals(("neqe-;ew22")));
    }

}
