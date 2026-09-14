using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long length, string fillchar) {
        long size = text.Length;
        StringBuilder sb = new StringBuilder(text);
        while (sb.Length < length)
        {
            sb.Insert(0, fillchar);
            if (sb.Length < length)
            {
                sb.Append(fillchar);
            }
        }
        return sb.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("magazine"), (25L), (".")).Equals((".........magazine........")));
    }

}
