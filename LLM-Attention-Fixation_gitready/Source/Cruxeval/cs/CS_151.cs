using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        StringBuilder sb = new StringBuilder();
        foreach (char c in text)
        {
            if (char.IsDigit(c))
            {
                if (c == '0')
                {
                    sb.Append('.');
                }
                else
                {
                    sb.Append(c == '1' ? '0' : c);
                }
            }
            else
            {
                sb.Append(c);
            }
        }
        return sb.ToString().Replace('.', '0');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("697 this is the ultimate 7 address to attack")).Equals(("697 this is the ultimate 7 address to attack")));
    }

}
