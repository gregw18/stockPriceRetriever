import {ItemsTable} from "../src/components/ItemsTable";
import './App.css';

export default function App() {
  console.log("starting app");
  let t0 = performance.now();
  let result = (<>
              <ItemsTable/>
            </>
  );
  console.log("App took ", performance.now() - t0, " ms., calling GenerateTable");
  return result;
}