using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string full, string part) {
        int length = part.Length;
        int index = full.IndexOf(part);
        int count = 0;
        while (index >= 0) {
            full = full.Substring(index + length);
            index = full.IndexOf(part);
            count++;
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hrsiajiajieihruejfhbrisvlmmy"), ("hr")) == (2L));
    }

}
