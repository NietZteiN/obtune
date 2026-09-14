using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, string old, string newStr) {
        int index = text.LastIndexOf(old, text.IndexOf(old));
        List<char> result = new List<char>(text.ToCharArray());
        while (index > 0)
        {
            result.RemoveRange(index, old.Length);
            result.InsertRange(index, newStr.ToCharArray());
            index = text.LastIndexOf(old, index);
        }
        return new string(result.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("jysrhfm ojwesf xgwwdyr dlrul ymba bpq"), ("j"), ("1")).Equals(("jysrhfm ojwesf xgwwdyr dlrul ymba bpq")));
    }

}
