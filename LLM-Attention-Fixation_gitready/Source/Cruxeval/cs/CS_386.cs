using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string concat, Dictionary<string,string> di) {
        int count = di.Count;
        for (int i = 0; i < count; i++) {
            if (di[i.ToString()]?.Contains(concat) == true) {
                di.Remove(i.ToString());
            }
        }
        return "Done!";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("mid"), (new Dictionary<string,string>(){{"0", "q"}, {"1", "f"}, {"2", "w"}, {"3", "i"}})).Equals(("Done!")));
    }

}
