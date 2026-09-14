using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string st) {
        st = st.ToLower();
        if (st.LastIndexOf('i', st.LastIndexOf('h')) >= st.LastIndexOf('i'))
        {
            return "Hey";
        }
        else
        {
            return "Hi";
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Hi there")).Equals(("Hey")));
    }

}
