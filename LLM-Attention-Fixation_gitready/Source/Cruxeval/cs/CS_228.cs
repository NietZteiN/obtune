using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string splitter) {
        return string.Join(splitter, text.ToLower().Split());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("LlTHH sAfLAPkPhtsWP"), ("#")).Equals(("llthh#saflapkphtswp")));
    }

}
