using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string line) {
        int count = 0;
        StringBuilder a = new StringBuilder();
        foreach (char c in line)
        {
            count++;
            if (count % 2 == 0)
            {
                a.Append(char.IsLetter(c) ? char.IsUpper(c) ? char.ToLower(c) : char.ToUpper(c) : c);
            }
            else
            {
                a.Append(c);
            }
        }
        return a.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("987yhNSHAshd 93275yrgSgbgSshfbsfB")).Equals(("987YhnShAShD 93275yRgsgBgssHfBsFB")));
    }

}
