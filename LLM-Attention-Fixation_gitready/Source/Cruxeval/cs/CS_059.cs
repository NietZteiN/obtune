using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        var a = s.Where(c => c != ' ').ToList();
        var b = new List<char>(a);
        for (int i = a.Count - 1; i >= 0; i--) {
            if (a[i] == ' ') {
                b.RemoveAt(i);
            } else {
                break;
            }
        }
        return string.Join("", b);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hi ")).Equals(("hi")));
    }

}
