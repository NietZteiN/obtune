using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        int a = text.Length;
        int count = 0;
        while (text.Length > 0)
        {
            if (text[0] == 'a')
            {
                count += text.IndexOf(' ');
            }
            else
            {
                count += text.IndexOf('\n');
            }
            int index = text.IndexOf('\n');
            if (index == -1)
            {
                break;
            }
            text = text.Substring(index + 1);
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a\nkgf\nasd\n")) == (1L));
    }

}
